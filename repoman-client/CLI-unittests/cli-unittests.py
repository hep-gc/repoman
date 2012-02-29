import re
import sys
import uuid
import unittest
from subprocess import Popen, PIPE, STDOUT


class RepomanCLITest(unittest.TestCase):
    """
    Base class for all Repoman CLI tests.
    """

    def setUp(self):
        # Nothing to do for now...
        pass

    def tearDown(self):
        # Nothing to do for now...
        pass

    def run_repoman_command(self, args):
        """
        This method will call the repoman application in a subprocess
        and pass it the given command line argument string.
        The output and the return code of the repoman invocation will be
        returned to the caller for further inspection.
        """
        try:
            cmd = 'repoman %s' % (args)
            print 'Running [%s]' % (cmd)
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            output = p.communicate()[0]
            return (output, p.returncode)
        except Exception, e:
            print 'Error running repoman command.\n%s' % (e)
            sys.exit(-1)
            

    def get_unique_image_name(self):
        """
        Use this method to easily create a unique image name to use in 
        your tests.
        """
        return str(uuid.uuid1())




#####################################################################
#####################################################################
#####################################################################
#
# Test cases implementation go here...
#
#

######################################################################
#		COMMAND - 'repoman version'
######################################################################
class ClientVersionTest(RepomanCLITest):
    def test_version(self):
        (output, returncode) = self.run_repoman_command('version')
        self.assertEqual(output, '0.3.11\n')
        self.assertEqual(returncode, 0)

######################################################################
#		COMMAND - 'repoman whoami'
######################################################################

class WhoamiTest(RepomanCLITest):
    def test_whoami(self):
        (output, returncode) = self.run_repoman_command('whoami')
        self.assertEqual(returncode, 0)

######################################################################

def CheckOptions(self, output, arg): 			
	"""
	CheckOptions method tests the common optional parameters for create-image and modify-image
	"""

	# If unauthenticated access is set as true or false while creating or modifying an image,
	# the status is checked in the output of 'repoman list-images' using regular expression 	
	if(arg == "--unauthenticated_access true" or arg == "-a true"):
		p = re.search('^\\s*unauthenticated_access : True\\s*$', output,flags=re.MULTILINE)
		self.assertTrue(p != None) 
	elif (arg == '--unauthenticated_access false' or arg == '-a false'):
                p = re.search('^\\s*unauthenticated_access : False\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)
	
	# If a description is given as "Random discription" while creating or modifying an image, 
	# the corresponding description is checked in the output of 'repoman list-images'
	elif (arg == '--description "Random description"' or arg == '--d "Random description"'):
		p = re.search('^\\s*description : Random description\\s*$', output, flags=re.MULTILINE)
		self.assertTrue(p != None)
	
	# If the hypervisor is set to or changed to a particular value (here 'xen'), it is checked in the output
	# of 'repoman list-images'
	elif (arg =='--hypervisor xen' or arg == '-h "xen"'):
		p = re.search('^\\s*hypervisor : xen\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)
	
	# If the Operating System Architecture is set to or changed to a particular value (here 'x86'),
	# the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_arch x86'):
                p = re.search('^\\s*os_arch : x86\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)

        # If the Operating System type is set to or changed to a particular value (here 'linux'),
        # the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_type linux'):
                p = re.search('^\\s*os_type : linux\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)

        # If the Operating System Variant is set to or changed to a particular value (here 'ubuntu'),
        # the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_variant ubuntu'):
                p = re.search('^\\s*os_variant : ubuntu\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)


######################################################################
#		COMMAND - 'repoman create-image'		     	
######################################################################



class CreateImageTest(RepomanCLITest):
    new_image_name = None
	
    """
    CreateImage method is called whenever the create-image command is used (with or without optional parameters)
    Optional parameters are stored in arg. 
    When create-image is called without options, arg is passed as an empty string
    """
	
    def CreateImage(self, arg):
        # Get a unique name for the new image we are going to create.
        # This will ensure it does not clash with any existing image on the
        # server.
        self.new_image_name = self.get_unique_image_name()
	
        # Now let's run the 'repoman create-image' command and check it's
        # output and exit code.
        (output, returncode) = self.run_repoman_command('create-image %s %s' % (self.new_image_name, arg))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)

        # Here we actually do a 'repoman list-image' to see if the image is
        # actually there.  We use a regular expression to inspect the output.
        (output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        m = re.search('^\\s+name : %s\\s*$' % (self.new_image_name), 
                      output, 
                      flags=re.MULTILINE)
        self.assertTrue(m != None)        
	
	CheckOptions(self, output, arg)


    def tearDown(self):
        # Delete the image we created to clean up properly after the test.
       	(output, returncode) = self.run_repoman_command('remove-image -f %s' % (self.new_image_name))

   
    def test_create_image(self):
	CreateImageTest.CreateImage(self,'')

    
    # Test the alias of create-image command ('repoman ci')	
    def test_ci(self):	
	self.new_image_name = self.get_unique_image_name()
	(output, returncode) = self.run_repoman_command('ci %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
	(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        m = re.search('^\\s+name : %s\\s*$' % (self.new_image_name),
                      output,
                      flags=re.MULTILINE)
        self.assertTrue(m != None)


	#########################################################
	#		OPTIONAL PARAMETERS			#	
	#########################################################

    # Test the optional parameter '--unauthenticated_access' or '-a', which can be set to true or false
    # Each case is in individual tests to ensure teardown (removing image after creating one)
    def test_create_image_unauthenticated_access_true(self):
	CreateImageTest.CreateImage(self,'--unauthenticated_access true')
    def test_create_image_a_true(self):		
	CreateImageTest.CreateImage(self,'-a true')
    def test_create_image_unauthenticated_access_false(self):
	CreateImageTest.CreateImage(self,'--unauthenticated_access false')       
    def test_create_image_a_false(self):   
	CreateImageTest.CreateImage(self,'-a false')


    # Test the optional parameter '--description' or '-d' 
    # The description given here is "Random description"
    def test_create_image_description(self):
	CreateImageTest.CreateImage(self, '--description "Random description"')
    def test_create_image_d(self):
        CreateImageTest.CreateImage(self, '--d "Random description"')
 
	
    # Test the optional parameter '--hypervisor' or '-h'
    # For this test, a random hypervisor ('xen') is selected
    def test_create_image_hypervisor(self):
	CreateImageTest.CreateImage(self, '--hypervisor xen')
    def test_create_image_h(self):
	CreateImageTest.CreateImage(self, '-h "xen"') 
	
    # Test the optional parameter '--os_arch'
    # For this test, a random operating system architecture ('x86') is selected
    def test_create_image_os_arch(self):
	CreateImageTest.CreateImage(self, '--os_arch x86')	

    # Test the optional parameter '--os_type'
    # For this test, a random operating system type ('linux') is selected
    def test_create_image_os_type(self):
        CreateImageTest.CreateImage(self, '--os_type linux')

    # Test the optional parameter '--os_variant'
    # For this test, a random operating system type ('ubuntu') is selected
    def test_create_image_os_variant(self):
        CreateImageTest.CreateImage(self, '--os_variant ubuntu')



######################################################################
#               COMMAND - 'repoman modify-image'                        
######################################################################

class ModifyImageTest(RepomanCLITest):
    new_image_name = None

    """
    ModifyImage function is called whenever the modify-image command is used (with or without optional parameters)
    Optional parameters are stored in arg. 
    When modify-image is called without options, arg is passed as an empty string
    """

    def ModifyImage(self, arg):
        # Get a unique name for the new image we are going to create.
        # This will ensure it does not clash with any existing image on the
        # server.
        self.new_image_name = self.get_unique_image_name()

        # Create a new image to be modified
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
	# Run 'repoman modify-image' and check the output
	(output, returncode) = self.run_repoman_command('modify-image %s %s' %(self.new_image_name, arg))
	self.assertEqual(output, "[OK]     Modifying image.\n")
	self.assertEqual(returncode, 0)
	
	(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
	CheckOptions(self, output, arg)
	
    def tearDown(self):
        # Delete the image we created to clean up properly after the test.
        (output, returncode) = self.run_repoman_command('remove-image -f %s' % (self.new_image_name))

    def test_modify_image(self):
	ModifyImageTest.ModifyImage(self, '')
    
    # Test the alias of modify-image ('repoman mi')		
    def test_mi(self):
	self.new_image_name = self.get_unique_image_name()
	 # Create a new image to be modified
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
        # Run 'repoman modify-image' and check the output
        (output, returncode) = self.run_repoman_command('mi %s' %(self.new_image_name))
        self.assertEqual(output, "[OK]     Modifying image.\n")
        self.assertEqual(returncode, 0)	


        #########################################################
        #               OPTIONAL PARAMETERS                     #       
        #########################################################

    # Test the optional parameter '--unauthenticated_access' or '-a', which can be set to true or false
    # Each case is in individual tests to ensure teardown (removing image after creating one)
    def test_modify_image_unauthenticated_access_true(self):
        ModifyImageTest.ModifyImage(self,'--unauthenticated_access true')
    def test_modify_image_a_true(self):
        ModifyImageTest.ModifyImage(self,'-a true')
    def test_modify_image_unauthenticated_access_false(self):
        ModifyImageTest.ModifyImage(self,'--unauthenticated_access false')
    def test_modify_image_a_false(self):
        ModifyImageTest.ModifyImage(self,'-a false')


    # Test the optional parameter '--description' or '-d' 
    # The description given here is "Random description"
    def test_modify_image_description(self):
        ModifyImageTest.ModifyImage(self, '--description "Random description"')
    def test_modify_image_d(self):
        ModifyImageTest.ModifyImage(self, '--d "Random description"')


    # Test the optional parameter '--hypervisor' or '-h'
    # For this test, a random hypervisor ('xen') is selected
    def test_modify_image_hypervisor(self):
        ModifyImageTest.ModifyImage(self, '--hypervisor xen')
    def test_modify_image_h(self):
        ModifyImageTest.ModifyImage(self, '-h "xen"')

    # Test the optional parameter '--os_arch'
    # For this test, a random operating system architecture ('x86') is selected
    def test_modify_image_os_arch(self):
        ModifyImageTest.ModifyImage(self, '--os_arch x86')

    # Test the optional parameter '--os_type'
    # For this test, a random operating system type ('linux') is selected
    def test_modify_image_os_type(self):
        ModifyImageTest.ModifyImage(self, '--os_type linux')

    # Test the optional parameter '--os_variant'
    # For this test, a random operating system type ('ubuntu') is selected
    def test_modify_image_os_variant(self):
        ModifyImageTest.ModifyImage(self, '--os_variant ubuntu')



#####################################################################
#####################################################################
#####################################################################




#
# The entrypoint into the script.
# No need to modify this at this point.
#

if __name__ == '__main__':
    unittest.main()

